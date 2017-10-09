import requests, pytest, re
ROOT = 'http://127.0.0.1:8080/rest'
NODES = set()
FILES = {'file': open('./image.jpg', 'rb')}

def test_
    # Ensure ROOT is accessible.
    r = requests.get(ROOT)
    assert r.status_code == 200
except AssertionError:
    print('Fedora root not found. Is Fedora running at the ROOT url?')

# POST
try:
    # Can create RDF resources
    r = requests.post(ROOT)
    assert r.status_code == 201
    NODES.add(r.headers['Location'])
except AssertionError:
    print('3.3 POST: Error creating an RDF resource')

try:
    # Creating an RDF resource returns constraints
    r = requests.post(ROOT)
    assert r.status_code == 201
    assert 'rel="http://www.w3.org/ns/ldp#constrainedBy"' in r.headers['Link']
    NODES.add(r.headers['Location'])
except AssertionError:
    print('3.3 POST: Constraints link missing when creating an RDF resource')

try:
    # Can create non-RDF resources
    r = requests.post(ROOT, files=FILES)
    assert r.status_code == 201
    NODES.add(r.headers['Location'])
except AssertionError:
    print('3.3 POST: Error creating non-RDF resource')

try:
    # Creating a non-RDF resource returns constraints
    r = requests.post(ROOT, files=FILES)
    assert r.status_code == 201
    NODES.add(r.headers['Location'])
    assert 'rel="http://www.w3.org/ns/ldp#constrainedBy"' in r.headers['Link']
except AssertionError:
    print('3.3 POST: Constraints link missing when creating a non-RDF resource')

try:
    # Creating a non-RDF resource returns its RDF description resource
    r = requests.post(ROOT, files=FILES)
    assert r.status_code == 201
    NODES.add(r.headers['Location'])
    assert 'rel="describedby"' in r.headers['Link']
except AssertionError:
    print('3.3 POST: Link to RDF description resource missing from non-RDF resource creation response')

try:
    # Creating a non-RDF resource returns its RDF description resource
    r = requests.post(ROOT, files=FILES)
    assert r.status_code == 201
    NODES.add(r.headers['Location'])
    describes_nr = re.search('<(\S+)>; ?rel="describedby"', r.headers['Link'])
    assert describes_nr is not None
    # group(1) is the captured group (\S+)
    r = requests.get(describes_nr.group(1))
    assert r.status_code == 200
    # TODO: Assert it has type ldp#RDFSource
except AssertionError:
    print('3.3 POST: RDF description resource not created for non-RDF resource')

try:
    # Non-RDF resource with bad digest value returns 409
    r = requests.post(ROOT, files=FILES, headers={'digest': 'md5=deadbeef'})
    assert r.status_code == 409
    #assert 'Checksum Mismatch' in r.text
except AssertionError:
    print('3.3.1 POST: Creating non-RDF resource with bad digest value works')

try:
    # Non-RDF resource with bad digest algorithm returns 400
    # TODO: How to query for accepted algorithms?
    r = requests.post(ROOT, files=FILES, headers={'digest': 'md1=fakealgo'})
    assert r.status_code == 400
    #assert 'Unsupported Digest Algorithm' in r.text
except AssertionError:
    print('3.3.1 POST: Creating non-RDF resource with bad digest algorithm works')

try:
    # Create with remote content
    pass
except AssertionError:
    print('POST: Remote content not supported')

# GET
# Set up
r = requests.post(ROOT)
r.raise_for_status
rs = r.headers['Location']
NODES.add(rs)
r = requests.post(rs)
r.raise_for_status
rs_contained = r.headers['Location']
NODES.add(rs_contained)
r = requests.post(ROOT, files=FILES)
r.raise_for_status
nr = r.headers['Location']
NODES.add(nr)

try:
    # A RDF resource links to the non-RDF resource it describes, if any
    r = requests.get(nr)
    describes_nr = re.search('<(\S+)>; ?rel="describedby"', r.headers['Link']).group(1)
    r = requests.get(describes_nr)
    assert r.status_code == 200
    assert re.search('<'+nr+'>; ?rel="describes"', r.headers['Link']) is not None
except AssertionError:
    print('3.5 GET: RDF resource describing a non-RDF resource does not link to that non-RDF resource')

try:
    # RDF resource responds to the Prefer header
    # TODO: How to query for Prefer header values?
    # TODO: Preference-Applied header always returned.
    r = requests.get(rs, headers={'Prefer': 'return=representation'})
    assert r.status_code == 200
    assert r.headers['Preference-Applied'] == 'return=representation'
    r = requests.get(rs, headers={'Prefer': 'return=minimal'})
    assert r.status_code == 200
    assert r.headers['Preference-Applied'] == 'return=minimal'
except AssertionError:
    print('3.5.2 GET: Preference-Applied header missing from response')

try:
    # RDF resource returns contained descriptions when asked
    r = requests.get(rs, headers={'Prefer': 'return=representation; include="http://w3.org/ns/oa#PreferContainedDescriptions"'})
    assert r.status_code == 200
    assert re.search('ldp:contains\s*<'+rs_contained+'>', r.text) is not None
    assert re.search('fedora:hasParent\s*<'+rs+'>', r.text) is not None
except AssertionError:
    print('3.5.1 GET: (MAY) Contained descriptions missing from response')

try:
    # RDF resource returns inbound references when asked
    r = requests.get(rs, headers={'Prefer': 'return=representation; include="http://fedora.info/definitions/fcrepo#PreferInboundReferences"'})
    assert r.status_code == 200
    # TODO: how to test inbound refs?
    raise AssertionError
except AssertionError:
    print('3.5.1 GET: (SHOULD) Inbound references missing from response')

try:
    # Non-RDF resource responds to the Want-Digest header.
    r = requests.get(nr, headers={'Want-Digest': 'md5'})
    assert r.status_code == 200
    assert r.headers['Digest'].startswith('md5=')
    r = requests.get(nr, headers={'Want-Digest': 'sha1'})
    assert r.status_code == 200
    assert r.headers['Digest'].startswith('sha1=')
except AssertionError:
    print('3.5.3 GET: Want-Digest header ignored or incorrect response returned')

# HEAD
try:
    # Head request has no body
    r = requests.head(ROOT)
    assert r.status_code == 200
    assert r.text == ''
    r = requests.head(nr, headers={'Want-Digest': 'sha1'})
    assert r.status_code == 200
    assert r.headers['Digest'].startswith('sha1=')
    assert r.text == ''
except AssertionError:
    print('3.6 HEAD: Unexpected response body for HEAD request')

# PUT

# PATCH

# DELETE
# Set up
DELETE_SUPPORTED = True
r = requests.post(ROOT)
r.raise_for_status
rs = r.headers['Location']
NODES.add(rs)
r = requests.post(rs)
r.raise_for_status
child = r.headers['Location']
NODES.add(child)
r = requests.post(child)
r.raise_for_status
grandchild = r.headers['Location']
NODES.add(grandchild)

try:
    # TODO: How to query for DELETE support?
    pass
except AssertionError:
    print('3.7 DELETE: (OPTIONAL) Delete method not supported')
    DELETE_SUPPORTED = False

if DELETE_SUPPORTED:
    try:
        # Support deletion with depth of zero
        # TODO: Depth of zero only supported for non-RDF resources?
        # TODO: How to query for supported or default Depth values?
        r = requests.delete(rs, headers={'Depth': '0'})
        assert r.status_code == 204
        r = requests.get(rs)
        assert r.status_code == 410
        r = requests.get(child)
        assert r.status_code == 200
    except AssertionError:
        print('3.7.1 DELETE: Depth: 0 not supported')

    try:
        # Support deletion with depth of infinity
        r = requests.delete(child, headers={'Depth': 'infinity'})
        assert r.status_code == 204
        r = requests.get(child)
        assert r.status_code == 410
        r = requests.get(grandchild)
        assert r.status_code == 410
    except AssertionError:
        print('3.7.1 DELETE: Depth: infinity not supported')

# Clean up
for node in NODES:
    r = requests.delete(node)
    r = requests.delete(node+'/fcr:tombstone')
